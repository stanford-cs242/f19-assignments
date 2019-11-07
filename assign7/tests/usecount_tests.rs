extern crate lib;
use lib::usecount::*;
use lib::executor::*;
use lib::future::*;
use std::sync::{Mutex, Arc};

/* UNCOMMENT BELOW TO RUN TESTS
#[test]
fn usecount_basic() {
  let mut uc: UseCounter<i32> = UseCounter::new(1);

  let n: &mut i32 = &mut uc;
  *n += 1;

  let n: &i32 = &uc;
  let x = *n + 1;

  assert_eq!(x, 3);
  assert_eq!(uc.count(), 2);
}

#[test]
fn usecount_future() {
  let uc = Arc::new(Mutex::new(UseCounter::new(1)));
  let fut = map(
    immediate(uc.clone()),
    |uc| {
      let n: &mut i32 = &mut uc.lock().unwrap();
      *n += 1
    });

  let mut exec = SingleThreadExecutor::new();
  exec.spawn(fut);
  exec.wait();

  let uc = uc.lock().unwrap();
  let n: &i32 = &uc;
  assert!(uc.count() == 2);
  assert!(*n == 2);
}
END */
