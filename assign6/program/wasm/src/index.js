const module_srcs = [
    require("buffer-loader!./basic.wat"),
    require("buffer-loader!./concat.wat"),
    require("buffer-loader!./funcall.wat"),
];
const wabt = require("wabt")();
const getTests = require("./tests");

// Utility function that returns a delay promise.
const delay = t => new Promise(resolve => setTimeout(resolve, t));
const waitTick = () => delay(0);

const modules =
  Promise.all(module_srcs)
         .then(wats => wats.map((wat) => wabt.parseWat("", wat)));

// Show WASM parsing error.
modules.catch(e =>
  $("#output").html(`<div class="alert alert-danger">
    <strong>Error while parsing wat files</strong>
  </div><pre><code>${e}</code></pre>`)
);

const validated = modules.then(modules => {
  modules.forEach((module) => {
    module.resolveNames();
    module.validate();
  });
  return modules;
});

// Show WASM validation error.
validated.catch(e =>
  $("#output").html(`<div class="alert alert-danger">
    <strong>Error while validating wat files</strong>
  </div><pre><code>${e}</code></pre>`)
);

// A promise that resolves to the binary WASM module.
const binaries = validated.then(
  modules => modules.map((module) => module.toBinary({ write_debug_names: true }).buffer)
);

var wasm_alloc = null;
var memory = null;

// Return a promise that resolves to the WASM module imports. This is
// done so that we can get a fresh allocator context each time.
const getModule = () =>
  Promise
    .all([binaries, import('wasm-alloc'), import('./memcpy.wasm')])
    .then(([buffers, wasm_alloc_, memcpy]) => {
      wasm_alloc = wasm_alloc_;
      memory = memcpy.memory;
      return buffers.map((buffer) => WebAssembly.instantiate(buffer, {
        "wasm-alloc": wasm_alloc,
        "memcpy": memcpy
      }));
    })

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
    .then((modules) => Promise.all(modules))
    .then((modules) => test(modules, memory, wasm_alloc))
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
    binaries.then(() => $("#progress").width("10%")).then(waitTick)
  )
  .then(() => delay(1000))
  .then(() => $("#progress-bar").fadeOut());
