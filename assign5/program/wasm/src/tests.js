const assert = require("chai").assert;

const PAGE_SIZE = 65536;

module.exports = function getTests(runTest) {
  let make_test = (n, r) => () => runTest(`mystery(${n}) = ${r}`, ({mystery}) => {
      assert.equal(mystery(n), r);
    });
  return [
    make_test(1, 1),
    make_test(3, 8),
    make_test(12, 10),
    make_test(100, 26),
    make_test(1000, 112)
  ]
};
