use rand::{rngs::SmallRng, SeedableRng, Rng};
use rlu::{RluSet, ConcurrentBTreeSet, ConcurrentSet};
use clap::{Arg, App};

use std::thread;
use std::time::Instant;

#[derive(Clone, Copy, Debug)]
enum SetType { Rlu, Bt }

impl<'a> From<&'a str> for SetType {
  fn from(s: &'a str) -> SetType {
    if s == "rlu" { SetType::Rlu }
    else if s == "bt" { SetType::Bt }
    else { unreachable!() }
  }
}

#[derive(Clone, Copy, Debug)]
struct BenchOpts {
  num_threads: usize,
  initial_size: usize,
  range: usize,
  timeout: u128,
  write_frac: f64,
  insert_frac: f64,
  num_iters: usize,
  set_type: SetType
}

fn set_readwrite<S>(set: S, opts: BenchOpts) -> usize
where S: ConcurrentSet<usize> + 'static
{
  let mut rng = SmallRng::from_seed([0; 16]);
  while set.len() < opts.initial_size {
    let i = rng.gen_range(0, opts.range);
    set.insert(i);
  }

  let worker = || {
    let set = set.clone_ref();
    thread::spawn(move || {
      let mut rng = SmallRng::from_seed([0; 16]);
      let start = Instant::now();
      let mut ops = 0;
      loop {
        if start.elapsed().as_millis() >= opts.timeout {
          break;
        }

        let i = rng.gen_range(0, opts.range);
        if rng.gen::<f64>() > opts.write_frac {
          set.contains(i);
        } else {
          if rng.gen::<f64>() > opts.insert_frac {
            set.insert(i);
          } else {
            set.delete(i);
          }
        }

        ops += 1;
      }

      ops
    })
  };

  let threads: Vec<_> = (0..opts.num_threads).map(|_| worker()).collect();
  threads.into_iter().map(|t| t.join().unwrap()).sum()
}

fn benchmark(opts: BenchOpts) {
  println!("write_frac,num_threads,throughput");

  for write_frac in &[0.02, 0.2, 0.4] {
    for num_threads in 1..=8 {
      let opts = BenchOpts { write_frac: *write_frac, num_threads, ..opts };
      let ops: Vec<usize> = (0..opts.num_iters)
        .map(|_| {
          match opts.set_type {
            SetType::Rlu => set_readwrite(RluSet::new(), opts),
            SetType::Bt => set_readwrite(ConcurrentBTreeSet::new(), opts)
          }
        })
        .collect();

      let avg: f64 = (ops.iter().sum::<usize>() as f64)
        / (ops.len() as f64);
      let throughput = avg / ((opts.timeout / 1000) as f64);

      println!("{},{},{}", write_frac, num_threads, throughput);
    }
  }
}

fn main() {
  let matches = App::new("RLU benchmark")
    .arg(Arg::with_name("settype").short("s").possible_values(&["rlu", "bt"]).default_value("rlu"))
    .arg(Arg::with_name("timeout").short("t").default_value("10000"))
    .arg(Arg::with_name("num_iters").short("n").default_value("3"))
    .get_matches();

  let opts = BenchOpts {
    insert_frac: 0.5,
    initial_size: 256,
    range: 512,
    num_iters: matches.value_of("num_iters").unwrap().parse::<usize>().expect("Failed to parse num_iters"),
    timeout: matches.value_of("timeout").unwrap().parse::<u128>().expect("Failed to parse timeout"),
    set_type: SetType::from(matches.value_of("settype").unwrap()),
    num_threads: 0,
    write_frac: 0.
  };

  benchmark(opts);
}
