extern crate take_mut;
extern crate lib;
use lib::future::*;

//Basic
#[test]
fn test_join() {
  let f1 = immediate(5);
  let f2 = immediate(6);
  let mut f3 = join(f1, f2);
  loop {
    let res = f3.poll();
    if let Poll::Ready(x) = res {
      assert_eq!(x, (5, 6));
      break;
    }
  }
}
#[test]
fn test_and_then() {
  let f1 = map(immediate(3), |n| n * 2);
  let f2 = |n| immediate(n + 4);
  let mut f3 = and_then(f1, f2);
  loop {
    let res = f3.poll();
    if let Poll::Ready(x) = res {
      assert_eq!(x, 10);
      break;
    }
  }
}
#[test]
fn test_both() {
  let f1 = map(immediate(3), |n| n * 2);
  let f2 = |n| immediate(n + 1);
  let f3 = immediate("Future");
  let f4 = and_then(f1, f2);
  let mut f5 = join(f3, f4);
  loop {
    let res = f5.poll();
    if let Poll::Ready(x) = res {
      assert_eq!(x, ("Future", 7));
      break;
    }
  }
}
//Hidden
#[test]
fn test_join2() {
  let f1 = immediate(-8);
  let f2 = immediate("Future");
  let mut f3 = join(f1, f2);
  loop {
    let res = f3.poll();
    if let Poll::Ready(x) = res {
      assert_eq!(x, (-8, "Future"));
      break;
    }
  }
}
#[test]
fn test_join3() {
  let f1 = immediate(3);
  let f2 = map(immediate(3), |n| n + 1);
  let mut f3 = join(f1, f2);
  loop {
    let res = f3.poll();
    if let Poll::Ready(x) = res {
      assert_eq!(x, (3, 4));
      break;
    }
  }
}

#[test]
fn test_and_then_2() {
  let f1 = map(immediate(3), |n| n * 2);
  let f2 = |n| immediate(n + 1);
  let mut f3 = and_then(f1, f2);
  loop {
    let res = f3.poll();
    if let Poll::Ready(x) = res {
      assert_eq!(x, (7));
      break;
    }
  }
}
#[test]
fn test_both_2() {
  let f1 = map(immediate(3), |n| n * 2);
  let f2 = map(immediate(3), |n| n + 1);
  let f3 = join(f1, f2);
  let f4 = |(a, b)| immediate(a + b);
  let mut f5 = and_then(f3, f4);

  loop {
    let res = f5.poll();
    if let Poll::Ready(x) = res {
      assert_eq!(x, (10));
      break;
    }
  }
}
