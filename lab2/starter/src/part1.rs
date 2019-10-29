use std::{ptr, io};
use std::collections::HashSet;

fn password_checker(s: String) {
  let mut guesses = 0;
  loop {
    let mut buffer = String::new();
    if let Err(_) = io::stdin().read_line(&mut buffer) { return; }
    if buffer.len() == 0 { return; }

    // If the buffer is "Password1" then print "You guessed it!" and return,
    // otherwise print the number of guesses so far.
    unimplemented!()
  }
}

fn add_n(v: Vec<i32>, n: i32) -> Vec<i32> {
  unimplemented!()
}

fn add_n_inplace(v: &mut Vec<i32>, n: i32) {
  unimplemented!()
}

fn dedup(v: &mut Vec<i32>) {
  unimplemented!()
}

#[cfg(test)]
mod test {
  use super::*;

  #[test]
  fn test_password_checker() {
    //password_checker(String::from("Password1"));
  }

  #[test]
  fn test_add_n() {
    assert_eq!(add_n(vec![1], 2), vec![3]);
  }

  #[test]
  fn test_add_n_inplace() {
    let mut v = vec![1];
    add_n_inplace(&mut v, 2);
    assert_eq!(v, vec![3]);
  }

  #[test]
  fn test_dedup() {
    let mut v = vec![3, 1, 0, 1, 4, 4];
    dedup(&mut v);
    assert_eq!(v, vec![3, 1, 0, 4]);
  }
}
