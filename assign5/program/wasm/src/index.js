const wat = require("buffer-loader!./mystery.wat");
const wabt = require("wabt")();
const getTests = require("./tests");

// Utility function that returns a delay promise.
const delay = t => new Promise(resolve => setTimeout(resolve, t));
const waitTick = () => delay(0);

const module = Promise.resolve(wat).then(wat => wabt.parseWat("mystery.wat", wat));

// Show WASM parsing error.
module.catch(e =>
  $("#output").html(`<div class="alert alert-danger">
    <strong>Error While Parsing mystery.wat</strong>
  </div><pre><code>${e}</code></pre>`)
);

const validated = module.then(module => {
  module.resolveNames();
  module.validate();
  return module;
});

// Show WASM validation error.
validated.catch(e =>
  $("#output").html(`<div class="alert alert-danger">
    <strong>Error while validating mystery.wat</strong>
  </div><pre><code>${e}</code></pre>`)
);

// A promise that resolves to the binary WASM module.
const binary = validated.then(
  module => module.toBinary({ write_debug_names: false }).buffer
);

// Return a promise that resolves to the WASM module imports. This is
// done so that we can get a fresh allocator context each time.
const getModule = () =>
  binary
    .then(buffer => WebAssembly.instantiate(buffer, {}))
    .then(result => result.instance.exports);

const formatError = e => {
  let message = e.toString();
  if (e.showDiff) {
    message += "\nExpected: " + JSON.stringify(e.expected, undefined, 2);
    message += "\nActual: " + JSON.stringify(e.actual, undefined, 2);
  }
  return message;
};

// Get the wasm module and run it's imports through `test`, writing results
// to the output.
const runTest = (name, test) =>
  getModule()
    .then(test)
    .then(() =>
      $("#output").append(`<div class="alert alert-success">
        <span class="glyphicon glyphicon-ok" aria-hidden="true"></span>
        <strong>${name}</strong> passed.</div>`)
    )
    .catch(e =>
      $("#output").append(`<div class="alert alert-danger">
        <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>
        <strong>${name}</strong> failed. <br><br> <pre>${formatError(
        e
      )}</pre></div>`)
    )
    .then(waitTick);

// The list of tests to execute.
const tests = getTests(runTest);

// Execute tests.
tests
  .reduce(
    (acc, test, i) =>
      acc.then(test).then(() => {
        let progress = 10 + ((i + 1) / tests.length) * 90;
        $("#progress").width(`${progress}%`);
      }),
    binary.then(() => $("#progress").width("10%")).then(waitTick)
  )
  .then(() => delay(1000))
  .then(() => $("#progress-bar").fadeOut());
