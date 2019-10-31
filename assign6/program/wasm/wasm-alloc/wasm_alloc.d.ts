/* tslint:disable */
/**
*/
export function alloc_init(): void;
/**
* @param {number} n 
* @returns {number} 
*/
export function alloc(n: number): number;
/**
* @param {number} ptr 
*/
export function dealloc(ptr: number): void;
/**
* @returns {number} 
*/
export function count(): number;
