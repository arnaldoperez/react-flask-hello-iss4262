const apiUrl = process.env.BACKEND_URL + "/api"
const getState = ({ getStore, getActions, setStore }) => {
  return {
    store: {
      message: null,
      demo: [
        {
          title: "FIRST",
          background: "white",
          initial: "white"
        },
        {
          title: "SECOND",
          background: "white",
          initial: "white"
        }
      ],
      token: null,
      userInfo: null,
      profilePicture: null
    },
    actions: {
      // Use getActions to call a function within a fuction
      exampleFunction: () => {
        getActions().changeColor(0, "green");
      },

      getMessage: async () => {
        try {
          // fetching data from the backend
          const resp = await fetch(process.env.BACKEND_URL + "/api/hello")
          const data = await resp.json()
          setStore({ message: data.message })
          // don't forget to return something, that is how the async resolves
          return data;
        } catch (error) {
          console.log("Error loading message from backend", error)
        }
      },
      changeColor: (index, color) => {
        //get the store
        const store = getStore();

        //we have to loop the entire demo array to look for the respective index
        //and change its color
        const demo = store.demo.map((elm, i) => {
          if (i === index) elm.background = color;
          return elm;
        });

        //reset the global store
        setStore({ demo: demo });
      },
      login: async (email, password) => {
        let resp = await fetch(apiUrl + "/login", {
          method: "POST",
          body: JSON.stringify({ email, password }),
          headers: {
            "Content-Type": "application/json"
          }
        })
        if (!resp.ok) {
          setStore({ token: null })
          return false
        }
        let data = await resp.json()
        setStore({ token: data.token, profilePicture: data.profilePicture })
        localStorage.setItem("token", data.token)
        return true
      },
      loadSession: async () => {
        let storageToken = localStorage.getItem("token")
        if (!storageToken) return
        let resp = await fetch(apiUrl + "/userinfo", {
          headers: {
            "Authorization": "Bearer " + storageToken
          }
        })
        if (!resp.ok) {
          setStore({ token: null })
          localStorage.removeItem("token")
          return false
        }
        let data = await resp.json()
        setStore({ userInfo: data, profilePicture: data.profilePicture, token: storageToken })
        return true
      },
      uploadProfilePicture: async (formData) => {
        let { token } = getStore()
        let resp = await fetch(apiUrl + "/profilepic", {
          method: "PUT",
          headers: {
            "Authorization": "Bearer " + token
          },
          body: formData
        })
        if (!resp.ok) return false
        let data = await resp.json()
        setStore({ profilePicture: data.profilePicture })
        return true
      },
      logout: async () => {
        let { token } = getStore()
        let resp = await fetch(apiUrl + "/logout", {
          method: "POST",
          headers: {
            "Authorization": "Bearer " + token,
            "Access-Control-Allow-Origin": "*"
            /* 
             has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
             If an opaque response serves your needs, set the request's mode to 'no-cors' to fetch the resource with CORS disabled.
            */
          }
        })
        if (!resp.ok) return false

        setStore({ token: null, userInfo: null, profilePicture: "" })
        localStorage.removeItem("token")
        return true
      }
    }
  };
};

export default getState;
