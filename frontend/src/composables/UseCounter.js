// useCounter.js
import { ref, readonly } from 'vue'

export default function useCounter() {
  const count = ref(0)
  const increment = () => { count.value += 1 }
  const decrement = () => { count.value -= 1 }
  const set = (val) => { count.value = val }
  const reset = () => { count.value = 0 }

  return {
    count: readonly(count),
    increment,
    decrement,
    set,
    reset
  }
}