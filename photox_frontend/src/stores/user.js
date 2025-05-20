import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    isLoggedIn: false
  }),
  actions: {
    setUser(userData) {
      this.user = userData
      this.isLoggedIn = true
      localStorage.setItem('user', JSON.stringify(userData))
    },
    logout() {
      this.user = null
      this.isLoggedIn = false
      localStorage.removeItem('user')
    },
    initialize() {
      const user = localStorage.getItem('user')
      if (user) {
        this.user = JSON.parse(user)
        this.isLoggedIn = true
      }
    }
  }
})  