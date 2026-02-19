/**
 * Provides classes for modeling Linux kernel dynamic memory allocation
 * via the kmalloc family of functions.
 *
 * `KmallocCall` wraps calls to kmalloc/kzalloc/kvmalloc and exposes
 * the size argument, GFP flags, and the struct being allocated.
 *
 * `FlexibleArrayMember` identifies trailing zero-length or unsized
 * array fields used as variable-length tails in kernel structs.
 *
 * Ported from google/security-research (Apache-2.0 License).
 */

import cpp

/**
 * A struct field that is a flexible array member — the last field
 * in a struct with either no size or size 0/1.
 *
 * These are commonly used in the kernel for variable-length data:
 * ```c
 * struct msg {
 *     int len;
 *     char data[];  // flexible array member
 * };
 * ```
 */
class FlexibleArrayMember extends Field {
  FlexibleArrayMember() {
    exists(Struct s |
      this =
        s.getCanonicalMember(max(int j |
            s.getCanonicalMember(j) instanceof Field
          |
            j
          ))
    ) and
    this.getUnspecifiedType() instanceof ArrayType and
    (
      this.getUnspecifiedType().(ArrayType).getArraySize() <= 1 or
      not this.getUnspecifiedType().(ArrayType).hasArraySize()
    )
  }
}

/**
 * A call to one of the kmalloc family of allocation functions:
 * `kmalloc`, `kzalloc`, or `kvmalloc`.
 */
class KmallocCall extends FunctionCall {
  KmallocCall() { this.getTarget().hasName(["kmalloc", "kzalloc", "kvmalloc"]) }

  /** Gets the size argument expression (first parameter). */
  Expr getSizeArg() { result = this.getArgument(0) }

  /** Gets the GFP flag string from the second argument. */
  string getFlag() {
    result =
      concat(Expr flag |
        flag = this.getArgument(1).getAChild*() and
        flag.getValueText().matches("%GFP%")
      |
        flag.getValueText(), "|"
      )
  }

  /**
   * Gets the numeric size as a string if constant,
   * or `"unknown"` for dynamic sizes.
   */
  string getSize() {
    if this.getSizeArg().isConstant()
    then result = this.getSizeArg().getValue()
    else result = "unknown"
  }

  /** Gets the type operand of a sizeof expression. */
  private Type sizeofParam(Expr e) {
    result = e.(SizeofExprOperator).getExprOperand().getFullyConverted().getType()
    or
    result = e.(SizeofTypeOperator).getTypeOperand()
  }

  /**
   * Gets the struct being allocated, inferred from sizeof()
   * expressions in the size argument.
   */
  Struct getStruct() {
    exists(Expr sof |
      this.getSizeArg().getAChild*() = sof and
      this.sizeofParam(sof) = result
    )
  }

  /**
   * Holds `"true"` if the allocation has a dynamic size and the
   * struct contains a flexible array member; `"false"` otherwise.
   */
  string isFlexible() {
    this.getSize() = "unknown" and
    this.getStruct().getAField() instanceof FlexibleArrayMember and
    result = "true"
    or
    not (
      this.getSize() = "unknown" and
      this.getStruct().getAField() instanceof FlexibleArrayMember
    ) and
    result = "false"
  }
}
