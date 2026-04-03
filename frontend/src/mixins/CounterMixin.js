// CounterMixin.js
export default {
    data() {
      return { count: 0 }
    },
    methods: {
      increment() {
        this.count++
      },
      decrement() {
        this.count--
      },
      set(val) {
        this.count = val
      },
      reset() {
        this.count = 0
      }
    }
  }