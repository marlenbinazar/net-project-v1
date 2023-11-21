import firebase from 'firebase/app';
import 'firebase/auth';

// Create Google provider
var provider = new firebase.auth.GoogleAuthProvider();

function signInWithGoogle() {
    // Sign in with Google using redirect
    firebase.auth()
        .signInWithRedirect(provider);
}

// Additional code for getting the redirect result
function handleRedirectResult() {
    firebase.auth()
        .getRedirectResult()
        .then((result) => {
            // This block will be executed when the user successfully signs in with Google
            var user = result.user;
            console.log('Google user signed in (redirect):', user);
        })
        .catch((error) => {
            // This block will be executed if there is an error during the redirect process
            var errorCode = error.code;
            var errorMessage = error.message;
            console.error('Google sign-in error (redirect):', errorCode, errorMessage);
        });
}

// Additional code for signing out
function signOut() {
    firebase.auth().signOut().then(() => {
        // Sign-out successful.
        console.log('User signed out');
    }).catch((error) => {
        // An error happened.
        console.error('Sign-out error:', error);
    });
}

// Call the function to handle redirect result when the page loads
handleRedirectResult();