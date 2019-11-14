use std::marker::PhantomData;

pub struct UserId(PhantomData<()>);
pub fn login(_username: String, _password: String) -> Result<UserId, String> {
  Ok(UserId(PhantomData))
}
pub fn order(_user: &UserId, _amount: f64) -> Result<(), String> {
  Ok(())
}
