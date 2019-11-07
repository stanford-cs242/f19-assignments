extern crate take_mut;
extern crate lib;
extern crate tempfile;
use lib::asyncio::*;
use lib::executor::*;
use lib::future::*;
use lib::future_util::*;
use tempfile::NamedTempFile;
use std::io::Write;
use std::sync::{Mutex, Arc};


macro_rules! make_tmp {
  ($contents:expr) => {{
    let mut tmp = NamedTempFile::new().unwrap();
    {
      let f = tmp.as_file_mut();
      write!(f, $contents).unwrap();
      f.sync_all().unwrap();
    }
    tmp
  }}
}

//Basic
#[test]
fn test_asyncio() {
  let tmp = make_tmp!("1.23");
  let fut = FileReader::new(tmp.path().to_path_buf());
  let mut exec = BlockingExecutor::new();
  exec.spawn(map(fut, |s| {
    assert_eq!(s.unwrap(), "1.23");
    ()
  }));
  exec.wait();
}

#[test]
fn test_asyncio2() {
  let tmp = make_tmp!("foobar");
  let fut = FileReader::new(tmp.path().to_path_buf());

  let mut exec = SingleThreadExecutor::new();
  exec.spawn(map(fut, |s| {
    assert_eq!(s.unwrap(), "foobar");
    ()
  }));
  exec.wait();
}

#[test]
fn test_asyncio3() {
  let tmp1 = make_tmp!("foobar");
  let fut1 = FileReader::new(tmp1.path().to_path_buf());
  let tmp2 = make_tmp!("foobar");
  let fut2 = FileReader::new(tmp2.path().to_path_buf());

  let mut exec = MultiThreadExecutor::new(2);
  exec.spawn(map(fut1, |s| {
    assert_eq!(s.unwrap(), "foobar");
    ()
  }));
  exec.spawn(map(fut2, |s| {
    assert_eq!(s.unwrap(), "foobar");
    ()
  }));
  exec.wait();
}

#[test]
fn test_poll_asyncio() {
  let tmp = make_tmp!("foobar");
  let f1 = FileReader::new(tmp.path().to_path_buf());
  let f2 = Arc::new(Mutex::new(Counter { fut: f1, value: 0 }));
  let mut exec = BlockingExecutor::new();
  exec.spawn(map(f2.clone(), |_| ()));
  exec.wait();
  assert!(f2.lock().unwrap().value > 0);
}
