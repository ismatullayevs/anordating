
/**
 * Returns the underlying signal value updating it each time the signal value changes.
 * @param signal - a signal.
 */
export function useSignal<T>(state: {value: T}, signal: {
    (): T;
    sub(fn: (v: T) => void): VoidFunction;
}) {
    return signal.sub((value) => {
        state.value = value;
    });    
}