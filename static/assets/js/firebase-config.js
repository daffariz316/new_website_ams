import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, 
         GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// Your web app's Firebase configuration
 const firebaseConfig = {
    // apiKey: "AIzaSyCNCvmzPqBbMWSpC9i2ki4aixAZYXjHYpo",
    // authDomain: "amslogin-ed00a.firebaseapp.com",
    // projectId: "amslogin-ed00a",
    // storageBucket: "amslogin-ed00a.firebasestorage.app",
    // messagingSenderId: "644507183205",
    // appId: "1:644507183205:web:26fec546db7638e9927e8c",
    // measurementId: "G-4GWZGCEBST"
  };

  // Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

const db = getFirestore(app);

export { auth, provider, db };