import { reactive } from 'vue'

let id = 0

const state = reactive({
  notifications: []
})

export function useNotification() {
  const notify = ({ message, type = 'success', duration = 3000 }) => {
    console.log("notify called");
    const notification = {
      id: id++,
      message,
      type
    }

    state.notifications.push(notification)

    if (duration > 0) {
      setTimeout(() => {
        remove(notification.id)
      }, duration)
    }
  }

  const remove = (id) => {
    const index = state.notifications.findIndex(n => n.id === id)
    if (index !== -1) {
      state.notifications.splice(index, 1)
    }
  }

  return {
    notifications: state.notifications,
    notify,
    remove
  }
}