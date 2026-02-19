/**
 * Provides a class for Linux kernel functions with helpers for
 * detecting GCC attributes commonly used in the kernel.
 *
 * Key attributes:
 *  - `__init` / `__exit` place functions in `.init.text` / `.exit.text`
 *    sections that are freed after boot.
 *  - `__always_inline` forces inlining regardless of optimization level.
 *
 * Ported from mebeim/linux-kernel-experiments (MIT License).
 */

import cpp

/** A Linux kernel function with attribute-inspection predicates. */
class KernelFunc extends Function {
  /**
   * Holds if this function is declared with
   * `__attribute__((section(sec)))`.
   */
  bindingset[sec]
  predicate isInSection(string sec) {
    exists(Attribute a |
      a = this.getAnAttribute() and
      a.hasName("section") and
      a.getArgument(0).getValueText() = sec
    )
  }

  /** Holds if this function has `__attribute__((always_inline))`. */
  predicate isAlwaysInline() {
    exists(Attribute a |
      a = this.getAnAttribute() and
      a.hasName("always_inline")
    )
  }
}
