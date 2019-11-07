use future::*;
use std::sync::{Mutex, Arc};

impl<F> Future for Box<F>
where
  F: Future + ?Sized,
{
  type Item = F::Item;

  fn poll(&mut self) -> Poll<Self::Item> {
    (**self).poll()
  }
}

impl<F> Future for Arc<Mutex<F>>
where
  F: Future,
{
  type Item = F::Item;

  fn poll(&mut self) -> Poll<Self::Item> {
    (**self).lock().unwrap().poll()
  }
}

pub struct Counter<Fut> {
  pub fut: Fut,
  pub value: i32,
}

impl<Fut> Future for Counter<Fut>
where
  Fut: Future,
{
  type Item = Fut::Item;
  fn poll(&mut self) -> Poll<Self::Item> {
    self.value += 1;
    return self.fut.poll();
  }
}
