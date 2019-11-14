use std::marker::PhantomData;
use std::sync::mpsc::{channel, Sender, Receiver};
use std::marker;
use std::mem::transmute;
use std::sync::atomic::{AtomicBool, Ordering};
use std::cell::RefCell;
use rand::{thread_rng, prelude::ThreadRng, Rng};
use std::any::TypeId;

thread_local!(static RNG: RefCell<ThreadRng> = RefCell::new(thread_rng()));
thread_local!(pub static NOISY: AtomicBool = AtomicBool::new(false));
const DROP_PROB: f32 = 0.4;

pub type Buffer = Vec<u8>;

#[derive(Debug, Clone)]
pub struct Packet {
  pub buf: Buffer,
  pub seqno: usize
}

pub struct Send<T, S>(PhantomData<(T, S)>);
pub struct Recv<T, S>(PhantomData<(T, S)>);
pub struct Offer<Left, Right>(PhantomData<(Left, Right)>);
pub struct Choose<Left, Right>(PhantomData<(Left, Right)>);
pub struct Close;
pub struct Rec<S>(PhantomData<S>);
pub struct Z;
pub struct S<N>(PhantomData<N>);
pub struct Var<N>(PhantomData<N>);

pub trait HasDual {
  type Dual;
}

impl HasDual for Close {
  type Dual = Close;
}

impl<T, S> HasDual for Send<T, S> where S: HasDual {
  type Dual = Recv<T, S::Dual>;
}

impl<T, S> HasDual for Recv<T, S> where S: HasDual {
  type Dual = Send<T, S::Dual>;
}

impl<Left, Right> HasDual for Choose<Left, Right>
where Left: HasDual, Right: HasDual {
  type Dual = Offer<Left::Dual, Right::Dual>;
}

impl<Left, Right> HasDual for Offer<Left, Right>
where Left: HasDual, Right: HasDual {
  type Dual = Choose<Left::Dual, Right::Dual>;
}

impl<N> HasDual for Var<N> {
  type Dual = Var<N>;
}

impl<N> HasDual for S<N> {
  type Dual = S<N>;
}

impl HasDual for Z {
  type Dual = Z;
}

impl<S> HasDual for Rec<S> where S: HasDual {
  type Dual = Rec<S::Dual>;
}

pub struct Chan<Env, S> {
  pub sender: Sender<Box<u8>>,
  pub receiver: Receiver<Box<u8>>,
  pub _data: PhantomData<(Env, S)>,
}

impl<Env, S> Chan<Env, S> {
  unsafe fn write<T>(&self, x: T)
  where
    T: marker::Send + 'static,
  {
    let sender: &Sender<Box<T>> = transmute(&self.sender);
    sender.send(Box::new(x)).unwrap();
  }

  unsafe fn read<T>(&self) -> T
  where
    T: marker::Send + 'static,
  {
    let receiver: &Receiver<Box<T>> = transmute(&self.receiver);
    *receiver.recv().unwrap()
  }
}

impl<Env> Chan<Env, Close> {
  pub fn close(self) {}
}

impl<Env, T, S> Chan<Env, Send<T, S>>
where
  T: marker::Send + 'static,
{
  pub fn send(self, x: T) -> Chan<Env, S> {
    unsafe {
      self.write(x);
      transmute(self)
    }
  }
}

impl<Env, T, S> Chan<Env, Recv<T, S>>
where
  T: marker::Send + 'static,
{
  pub fn recv(self) -> (Chan<Env, S>, T) {
    NOISY.with(|noisy| {
      unsafe {
        let mut x = self.read();
        if noisy.load(Ordering::SeqCst) &&
          TypeId::of::<T>() == TypeId::of::<Vec<Packet>>()
        {
          let xmut = &mut x;
          let xmut: &mut Vec<Packet> = transmute(xmut);

          let mut rng = RNG.with(|gen| gen.borrow().clone());
          let mut idx = (0..xmut.len())
            .filter(|_| rng.gen_bool(DROP_PROB.into()))
            .collect::<Vec<_>>();
          idx.reverse();

          for i in idx {
            xmut.remove(i);
          }
        }

        (transmute(self), x)
      }
    })
  }
}

impl<Env, Left, Right> Chan<Env, Choose<Left, Right>> {
  pub fn left(self) -> Chan<Env, Left> {
    unsafe {
      self.write(true);
      transmute(self)
    }
  }

  pub fn right(self) -> Chan<Env, Right> {
    unsafe {
      self.write(false);
      transmute(self)
    }
  }
}

pub enum Branch<L, R> {
  Left(L),
  Right(R),
}

impl<Env, Left, Right> Chan<Env, Offer<Left, Right>> {
  pub fn offer(self) -> Branch<Chan<Env, Left>, Chan<Env, Right>> {
    unsafe {
      if self.read() {
        Branch::Left(transmute(self))
      } else {
        Branch::Right(transmute(self))
      }
    }
  }
}

impl<S> Chan<(), S> where S: HasDual {
  pub fn new() -> (Chan<(), S>, Chan<(), S::Dual>) {
    let (sender1, receiver1) = channel();
    let (sender2, receiver2) = channel();
    let c1 = Chan {
      sender: sender1,
      receiver: receiver2,
      _data: PhantomData,
    };
    let c2 = Chan {
      sender: sender2,
      receiver: receiver1,
      _data: PhantomData,
    };
    (c1, c2)
  }
}

impl<Env, S> Chan<Env, Rec<S>> {
  pub fn rec_push(self) -> Chan<(S, Env), S> {
    unsafe { transmute(self) }
  }
}

impl<Env, S> Chan<(S, Env), Var<Z>> {
  pub fn rec_pop(self) -> Chan<(S, Env), S> {
    unsafe { transmute(self) }
  }
}

impl<Env, Sigma, N> Chan<(Sigma, Env), Var<S<N>>> {
  pub fn rec_pop(self) -> Chan<Env, Var<N>> {
    unsafe { transmute(self) }
  }
}
