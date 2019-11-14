extern crate assign8;
use assign8::cart::*;

fn main() {
  let empty = Cart::login("A".into(), "B".into()).unwrap();
  empty.checkout();
}
