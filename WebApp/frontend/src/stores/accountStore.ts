import { ref, computed } from 'vue'
import { defineStore } from 'pinia'


export type UserProfileToken = {
  userName: string;
  email: string;
  token: string;
};

export type UserProfile = {
  userName: string;
  email: string;
};

export const useAccountStore = defineStore('account', () => {

  // state 
  const user = ref<UserProfileToken | null>(null);

  // getters
  const isAuthenticated  = computed(() => user.value !== null);

// Actions 
const setUser = (userData: UserProfileToken) => {
  user.value = userData;
  localStorage.setItem('user', JSON.stringify(userData)); // Persist data 
};

const logout = () => {
  user.value = null;
  localStorage.removeItem('user');
};

const loadUserFromStorage = () => {
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    user.value = JSON.parse(storedUser);
  }
};

return {
  user,
  isAuthenticated,
  setUser,
  logout,
  loadUserFromStorage,
};
});
