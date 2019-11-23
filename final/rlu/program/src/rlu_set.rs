use crate::concurrent_set::ConcurrentSet;
use std::fmt::Debug;
use std::marker::{Unpin, PhantomData};


pub struct RluSet<T> {
  /* Fill in fields here! */
  _marker: PhantomData<T> // Remove this
}

// In case you need raw pointers in your RluSet, you can assert that RluSet is definitely
// Send and Sync
unsafe impl<T> Send for RluSet<T> {}
unsafe impl<T> Sync for RluSet<T> {}

impl<T> RluSet<T> where T: PartialEq + PartialOrd + Copy + Clone + Debug + Unpin {
  pub fn new() -> RluSet<T> {
    unimplemented!()
  }


  pub fn to_string(&self) -> String {
    unimplemented!()
  }
}

impl<T> ConcurrentSet<T> for RluSet<T> where T: PartialEq + PartialOrd + Copy + Clone + Debug + Unpin {
  fn contains(&self, value: T) -> bool {
    unimplemented!()
  }

  fn len(&self) -> usize {
    unimplemented!()
  }

  fn insert(&self, value: T) -> bool {
    unimplemented!()
  }

  fn delete(&self, value: T) -> bool {
    unimplemented!()
  }

  fn clone_ref(&self) -> Self {
    unimplemented!()
  }
}
