extern crate lib;
use lib::executor::*;
use lib::future::*;
use lib::future_util::*;
use std::sync::{Mutex, Arc};

fn test_executor<T: Executor>(mut exec: T) {
  for _ in 0..100 {
    let f1 = immediate(5);
    let f2 = immediate(6);
    let f3 = join(f1, f2);
    exec.spawn(map(f3, |n| {
      assert_eq!(n, (5, 6));
      ()
    }));
  }
  exec.wait();
}

#[test]
fn blocking() {
  test_executor(BlockingExecutor::new());
}

#[test]
fn singlethread() {
  test_executor(SingleThreadExecutor::new());
}

#[test]
fn multithread() {
  test_executor(MultiThreadExecutor::new(4));
}

#[test]
fn arc_singlethread_test() {
  let f1 = immediate(5);
  let f = Arc::new(Mutex::new(Counter { fut: f1, value: 0 }));
  let mut exec = SingleThreadExecutor::new();
  exec.spawn(map(f.clone(), |_| ()));
  exec.wait();
  assert_eq!(f.lock().unwrap().value, 1);
}

#[test]
fn arc_multithread_test() {
  let f1 = immediate(5);
  let f = Arc::new(Mutex::new(Counter { fut: f1, value: 0 }));
  let mut exec = MultiThreadExecutor::new(3);
  exec.spawn(map(f.clone(), |_| ()));
  exec.wait();
  assert_eq!(f.lock().unwrap().value, 1);
}

#[test]
fn arc_singlethread_test2() {
  let f1 = immediate(5);
  let f2 = immediate(6);
  let f3 = join(f1, f2);
  let f = Arc::new(Mutex::new(Counter { fut: f3, value: 0 }));
  let mut exec = SingleThreadExecutor::new();
  exec.spawn(map(f.clone(), |_| ()));
  exec.wait();
  assert!(f.lock().unwrap().value <= 2);
}

#[test]
fn arc_multithread_test2() {
  let f1 = immediate(5);
  let f2 = immediate(6);
  let f3 = join(f1, f2);
  let f = Arc::new(Mutex::new(Counter { fut: f3, value: 0 }));
  let mut exec = MultiThreadExecutor::new(3);
  exec.spawn(map(f.clone(), |_| ()));
  exec.wait();
  assert!(f.lock().unwrap().value <= 2);
}

#[test]
fn arc_singlethread_test3() {
  let f1 = map(immediate(3), |n| n * 2);
  let f2 = |_n| map(immediate(0), |n| n + 4);
  let f3 = and_then(f1, f2);
  let f = Arc::new(Mutex::new(Counter { fut: f3, value: 0 }));
  let mut exec = SingleThreadExecutor::new();
  exec.spawn(map(f.clone(), |_| ()));
  exec.wait();
  assert!(f.lock().unwrap().value <= 2);
}

#[test]
fn arc_multithread_test3() {
  let f1 = map(immediate(3), |n| n * 2);
  let f2 = |_n| map(immediate(0), |n| n + 4);
  let f3 = and_then(f1, f2);
  let f = Arc::new(Mutex::new(Counter { fut: f3, value: 0 }));
  let mut exec = MultiThreadExecutor::new(3);
  exec.spawn(map(f.clone(), |_| ()));
  exec.wait();
  assert!(f.lock().unwrap().value <= 2);
}

#[test]
fn arc_singlethread_test4() {
  let f1 = map(immediate(3), |n| n * 2);
  let f = Arc::new(Mutex::new(Counter { fut: f1, value: 0 }));
  let mut exec = SingleThreadExecutor::new();
  exec.spawn(map(f.clone(), |_| ()));
  exec.wait();
  assert_eq!(f.lock().unwrap().value, 1);
}

#[test]
fn arc_multithread_test4() {
  let f1 = map(immediate(3), |n| n * 2);
  let f = Arc::new(Mutex::new(Counter { fut: f1, value: 0 }));
  let mut exec = MultiThreadExecutor::new(3);
  exec.spawn(map(f.clone(), |_| ()));
  exec.wait();
  assert_eq!(f.lock().unwrap().value, 1);
}

fn test_executor2<T: Executor>(mut exec: T) {
  let f1 = map(immediate(3), |n| n * 2);
  let f2 = map(immediate(3), |n| n + 1);
  let f3 = join(f1, f2);
  let f4 = |(a, b)| immediate(a + b);
  let f5 = and_then(f3, f4);
  exec.spawn(map(f5, |n| {
    assert_eq!(n, (10));
    ()
  }));
  exec.wait();
}

#[test]
fn singlethread2() {
  test_executor2(SingleThreadExecutor::new());
}

#[test]
fn multithread2a() {
  test_executor2(MultiThreadExecutor::new(3));
}

#[test]
fn multithread2b() {
  test_executor2(MultiThreadExecutor::new(1));
}
