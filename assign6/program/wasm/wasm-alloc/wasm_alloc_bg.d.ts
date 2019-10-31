/* tslint:disable */
export const memory: WebAssembly.Memory;
export function alloc_init(): void;
export function alloc(a: number): number;
export function dealloc(a: number): void;
export function count(): number;
export function __wbindgen_malloc(a: number): number;
export function __wbindgen_realloc(a: number, b: number, c: number): number;
export function __wbindgen_free(a: number, b: number): void;
