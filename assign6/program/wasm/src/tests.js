const assert = require("chai").assert;

const PAGE_SIZE = 65536;

let to_string = (mem, ptr, len) => {
  let s = "";
  for (let i = 0; i < len; ++i) {
    s += String.fromCharCode(mem[ptr+i]);
  }
  return s;
}

module.exports = function getTests(runTest) {
  let test_harness = (name, i, f) => () => runTest(name, (modules, memory, wasm_alloc) => {
    wasm_alloc.alloc_init();
    console.log(modules);
    f(modules[i].instance.exports.main(), new Uint32Array(memory.buffer));
    let remaining = wasm_alloc.count();
    if (remaining > 1) {
      assert.fail(`${remaining-1} memory allocations were leaked (not freed)`);
    }
  });

  return [
    test_harness('test_basic', 0, (ptr, mem) => {
      assert.equal(to_string(mem, ptr, 5), 'basic', 'Output of main was incorrect');
    }),
    test_harness('test_concat', 1, (ptr, mem) => {
      assert.equal(to_string(mem, ptr, 11), 'hello world', 'Output of main was incorrect');
    }),
    test_harness('test_funcall', 2, (ptr, mem) => {
      assert.equal(to_string(mem, ptr, 11), 'hello world', 'Output of main was incorrect');
    })
  ]
};
