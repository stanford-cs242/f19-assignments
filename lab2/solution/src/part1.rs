use std::{ptr, io};
use std::collections::HashSet;

fn password_checker(s: String) {
  let mut guesses = 0;
  loop {
    let mut buffer = String::new();
    if let Err(_) = io::stdin().read_line(&mut buffer) { return; }
    if buffer.len() == 0 { return; }

    if &buffer[0..(buffer.len()-1)] == &s {
      println!("You guessed it!");
      return;
    } else {
      println!("Guesses: {}", guesses + 1);
      guesses += 1;
    }
  }
}

fn add_n(v: Vec<i32>, n: i32) -> Vec<i32> {
  v.into_iter().map(|x| x + n).collect()
}

fn add_n_inplace(v: &mut Vec<i32>, n: i32) {
  for x in v.iter_mut() {
    *x = *x + n;
  }
}

fn dedup(v: &mut Vec<i32>) {
  let mut elts = HashSet::new();
  let mut to_delete = Vec::new();
  for i in 0 .. v.len() {
    if elts.contains(&v[i]) {
      to_delete.push(i);
    } else {
      elts.insert(v[i]);
    }
  }

  to_delete.reverse();
  for idx in to_delete {
    v.remove(idx);
  }
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
