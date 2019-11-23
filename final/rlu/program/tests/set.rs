extern crate rand;

use rlu::{RluSet, ConcurrentSet};
use std::thread;

use rand::{random, thread_rng, Rng};

#[test]
fn set_simple() {
  let set = RluSet::new();

  assert!(!set.contains(0));
  assert!(!set.delete(0));
  assert!(set.insert(2));
  println!("Ins 0: {}", set.to_string());

  assert!(set.insert(0));
  assert!(set.insert(1));
  println!("Ins 1: {}", set.to_string());

  for i in 0..=2 {
    assert!(set.contains(i));
  }

  assert!(!set.contains(5));
  println!("Contains");

  assert!(set.delete(1));
  println!("Del 1: {}", set.to_string());

  assert!(!set.contains(1));

  assert!(set.delete(0));
  assert!(!set.contains(0));

  assert!(set.delete(2));
  println!("Del 2: {}", set.to_string());
}

#[test]
fn set_thread() {
  let set = RluSet::new();

  for i in 0..1000 {
    assert!(set.insert(i));
  }

  let reader = || {
    let set = set.clone_ref();
    thread::spawn(move || {
      let mut rng = thread_rng();

      for _ in 0..10000 {
        let i = rng.gen_range(0, 500) * 2;
        assert!(set.contains(i));
      }
    })
  };

  let writer = || {
    let set = set.clone_ref();
    thread::spawn(move || {
      let mut rng = thread_rng();

      for _ in 0..1000 {
        let i = rng.gen_range(0, 499) * 2 + 1;
        if random() {
          set.insert(i);
        } else {
          set.delete(i);
        }
      }
    })
  };

  let readers: Vec<_> = (0..16).map(|_| reader()).collect();
  let writers: Vec<_> = (0..4).map(|_| writer()).collect();

  for t in readers {
    t.join().unwrap();
  }

  for t in writers {
    t.join().unwrap();
  }
}
