/**
 * @name Integer truncation in size calculations
 * @kind path-problem
 * @problem.severity error
 * @id cpp/linux/size-t-to-int-truncation
 * @description Finds data flow paths where a 64-bit unsigned value
 *              (size_t, u64, unsigned long) is narrowed to a 32-bit
 *              signed int before use in pointer arithmetic or array
 *              indexing. This truncation can cause heap overflows.
 * @tags security kernel taint
 */

import cpp
import semmle.code.cpp.dataflow.new.TaintTracking
import SizeTruncationFlow::PathGraph

/**
 * A parameter of unsigned 64-bit type — the taint source.
 * These represent sizes or offsets received from user space
 * or other subsystems.
 */
class WideUnsignedSource extends DataFlow::Node {
  WideUnsignedSource() {
    exists(Parameter p |
      this.asParameter() = p and
      p.getUnspecifiedType().getSize() >= 8 and
      p.getUnspecifiedType().isUnsigned()
    )
  }
}

/**
 * A narrowing cast or implicit conversion to a signed 32-bit
 * type used in pointer arithmetic or array indexing — the sink.
 */
class NarrowIntSink extends DataFlow::Node {
  NarrowIntSink() {
    exists(Expr e |
      this.asExpr() = e and
      e.getFullyConverted().getType().getSize() <= 4 and
      not e.getFullyConverted().getType().isUnsigned() and
      (
        e.getParent() instanceof PointerArithmeticOperation or
        e.getParent() instanceof ArrayExpr
      )
    )
  }
}

module SizeTruncationConfig implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) { source instanceof WideUnsignedSource }

  predicate isSink(DataFlow::Node sink) { sink instanceof NarrowIntSink }
}

module SizeTruncationFlow = TaintTracking::Global<SizeTruncationConfig>;

from SizeTruncationFlow::PathNode source, SizeTruncationFlow::PathNode sink
where SizeTruncationFlow::flowPath(source, sink)
select sink.getNode(), source, sink,
  "64-bit value from $@ truncated to int before pointer arithmetic", source.getNode(),
  source.getNode().toString()
