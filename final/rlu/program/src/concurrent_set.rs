pub trait ConcurrentSet<T>: Send + Sync {
  // Returns the number of elements in the set
  fn len(&self) -> usize;

  // Returns true if the value is contained in the set
  fn contains(&self, value: T) -> bool;

  // If the value is not in the set, insert it and return true, return false otherwise
  fn insert(&self, value: T) -> bool;

  // If the value is in the set, delete it and return true, return false otherwise
  fn delete(&self, value: T) -> bool;

  // Create a new owned reference to the same underlying set
  fn clone_ref(&self) -> Self;
}
