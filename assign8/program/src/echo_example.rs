use session::*;

type Server = Rec<Recv<String, Offer<Var<Z>, Close>>>;
type Client = <Server as HasDual>::Dual;

fn server(c: Chan<(), Server>) {
  let mut c = c.rec_push();
  loop {
    c = {
      let (c, s) = c.recv();
      println!("{}", s);
      match c.offer() {
        Branch::Left(c) => c.rec_pop(),
        Branch::Right(c) => {
          c.close();
          return;
        }
      }
    }
  }
}

fn client(c: Chan<(), Client>) {
  let mut c = c.rec_push();
  loop {
    c = {
      let c = c.send("echo!".to_string());
      c.left().rec_pop()
    }
  }
}

