use session::*;

type Id = String;
type AtmDeposit = Recv<u64, Send<u64, Var<Z>>>;
type AtmWithdraw = Recv<u64, Choose<Var<Z>, Close>>;
type AtmServer =
  Recv<Id,
  Choose<
    Rec<
      Offer<Offer<
        AtmDeposit,
        AtmWithdraw>,
        Close>>,
    Close>>;
type AtmClient = <AtmServer as HasDual>::Dual;

fn approved(_id: &str) -> bool { true }

pub fn atm_server(c: Chan<(), AtmServer>) {
  let (c, id) = c.recv();
  if !approved(&id) {
    c.right().close();
    return;
  }
  let mut balance = 100; // get balance for id

  let c = c.left();
  let mut c = c.rec_push();
  loop {
    c = match c.offer() {
      Branch::Left(c) =>  // Deposit or withdraw
        match c.offer() {
          Branch::Left(c) => { // Deposit
            let (c, amt) = c.recv();
            balance += amt;
            c.send(balance).rec_pop()
          }
          Branch::Right(c) => { // Withdraw
            let (c, amt) = c.recv();
            if balance >= amt {
              balance -= amt;
              c.left().rec_pop()
            } else {
              c.right().close();
              return;
            }
          }
        },
      Branch::Right(c) => { c.close(); return; } // Exit loop
    }
  }
}

pub fn atm_client(c: Chan<(), AtmClient>) {
  let id = String::from("wcrichto");
  let c = c.send(id);
  match c.offer() {
    Branch::Left(c) => {
      let c = c.rec_push().left().right(); // withdraw
      let c = c.send(105);
      match c.offer() {
        Branch::Left(c) => {
          println!("Withdrawl succeeded.");
          c.rec_pop().right().close();
        }
        Branch::Right(c) => {
          println!("Insufficient funds.");
          c.close()
        }
      }
    }
    Branch::Right(c) => {
      println!("Invalid authorization");
      c.close();
    }
  }
}
