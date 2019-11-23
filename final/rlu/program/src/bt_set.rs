use crate::concurrent_set::ConcurrentSet;
use std::collections::BTreeSet;
use std::sync::{Arc, RwLock};
use std::hash::Hash;

pub struct ConcurrentBTreeSet<T>(Arc<RwLock<BTreeSet<T>>>);

impl<T> ConcurrentBTreeSet<T> where T: Ord + Send + Sync {
  pub fn new() -> ConcurrentBTreeSet<T> {
    ConcurrentBTreeSet(Arc::new(RwLock::new(BTreeSet::new())))
  }
}

impl<T> ConcurrentSet<T> for ConcurrentBTreeSet<T> where T: Ord + Send + Sync {
  fn len(&self) -> usize {
    self.0.read().unwrap().len()
  }

  fn contains(&self, value: T) -> bool {
    self.0.read().unwrap().contains(&value)
  }

  fn insert(&self, value: T) -> bool {
    self.0.write().unwrap().insert(value)
  }

  fn delete(&self, value: T) -> bool {
    self.0.write().unwrap().remove(&value)
  }

  fn clone_ref(&self) -> Self {
    ConcurrentBTreeSet(self.0.clone())
  }
}
