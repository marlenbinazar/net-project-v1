import firebase from 'firebase/app';

var firebaseConfig = '{{ firebase_config|safe }}';
firebase.initializeApp(firebaseConfig);

