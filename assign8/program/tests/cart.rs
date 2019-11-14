extern crate assign8;
use assign8::cart::*;

#[test]
fn auth_test() {
  let _empty = Cart::login("A".into(), "B".into()).unwrap();
}

#[test]
fn additem_test() {
  let empty = Cart::login("A".into(), "B".into()).unwrap();
  let _nonempty = empty.additem(1.0);
}

#[test]
fn additem_twice_test() {
  let empty = Cart::login("A".into(), "B".into()).unwrap();
  let nonempty = empty.additem(1.0);
  let _nonempty = nonempty.additem(1.0);
}

#[test]
fn checkout_test() {
  let empty = Cart::login("A".into(), "B".into()).unwrap();
  let nonempty = empty.additem(1.0);
  let nonempty = nonempty.additem(1.0);
  let _checkout = nonempty.checkout();
}

#[test]
fn cancel_test() {
  let empty = Cart::login("A".into(), "B".into()).unwrap();
  let nonempty = empty.additem(1.0);
  let nonempty = nonempty.additem(1.0);
  let checkout = nonempty.checkout();
  let _nonempty = checkout.cancel();
}

#[test]
fn order_ok_test() {
  let empty = Cart::login("A".into(), "B".into()).unwrap();
  let nonempty = empty.additem(1.0);
  let nonempty = nonempty.additem(1.0);
  let checkout = nonempty.checkout();
  match checkout.order() {
    Ok(c) => { c.additem(1.0); }
    Err(_) => {}
  }
}

#[test]
fn order_err_test() {
  // Get a cart after logging in
  let empty = Cart::login(
    "username".to_string(), "password".to_string()).unwrap();
  // Cart becomes non empty after first item
  let nonempty = empty.additem(1.0);
  // Can continue adding items to cart
  let nonempty = nonempty.additem(1.0);
  // Checkout freezes cart from adding more items
  let checkout = nonempty.checkout();
  // After attempting to order, we either succeed and get back an
  // empty cart, or get an error and keep the checkout cart.
  match checkout.order() {
    Ok(cart) => {
      let _ = cart.additem(1.0);
    }
    Err((cart, err)) => {
      println!("{}", err);
      let _ = cart.order();
    }
  }
}

#[test]
fn cart_fail() {
  let t = trybuild::TestCases::new();
  t.compile_fail("tests/cart-fail/*.rs");
}
