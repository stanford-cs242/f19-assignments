use future::*;
use std::path::PathBuf;
use std::thread;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::fs;
use std::io;

pub struct FileReader {
  path: PathBuf,
  thread: Option<thread::JoinHandle<io::Result<String>>>,
  done_flag: Arc<AtomicBool>,
}

impl FileReader {
  pub fn new(path: PathBuf) -> FileReader {
    unimplemented!()
  }
}

impl Future for FileReader {
  type Item = io::Result<String>;

  fn poll(&mut self) -> Poll<Self::Item> {
    unimplemented!()
  }
}
