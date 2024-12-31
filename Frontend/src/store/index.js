import Vue from 'vue'
import Vuex from 'vuex'
Vue.use(Vuex)

const store = new Vuex.Store({
    state:{
        token:'',
        username:''
    },
    getters:{
        getToken(state){
            return state.token || localStorage.getItem("token") || "";
        },
        getUsername(state){
            return state.token || localStorage.getItem("token") || "";
        }
    },
    mutations: {
        // 修改token，并将token存入localStorage
        setToken(state,token) {
            state.token = token;
            localStorage.setItem('token', token);
        },
        delToken(state) {
            // state.token = "";
            // localStorage.removeItem("token");
            state.username = ""
            localStorage.removeItem("username");
        },
        // 可选
        setUserName(state, userName) {
            state.username = userName;
            localStorage.setItem('username', userName);
        }
    },
    actions:{}
});
export default store;