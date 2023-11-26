// TODO: Replace the following with your app's Firebase project configuration
const firebaseConfig = {
    apiKey: "AIzaSyAw6ZMNTM2S11i5fNuMKdVfI6s978wjR48",
    authDomain: "netshards-app.firebaseapp.com",
    databaseURL: "https://netshards-app-default-rtdb.firebaseio.com",
    projectId: "netshards-app",
    storageBucket: "netshards-app.appspot.com",
    messagingSenderId: "156715781087",
    appId: "1:156715781087:web:e877ce7c0e8fc55ab6126a",
    measurementId: "G-719L3Z33G7"
    //...
};

firebase.initializeApp(firebaseConfig);

var ui = new firebaseui.auth.AuthUI(firebase.auth());

export default firebase;

export {
    ui,
};