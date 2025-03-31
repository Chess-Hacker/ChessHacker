// This goes on Cloudflare

export default {
  async fetch(request, env, ctx) {

    // Check if the request has both required headers
    if(!request.headers.has("Token") || !request.headers.has("Action")) {
      return new Response(null, {
        status: 400, statusText: "Bad Request"
      });
    }

    let action = request.headers.get("Action");
    
    // Check if the requested action is valid
    if(action !== "Release" && action !== "Bind") {
      return new Response(null, {
        status: 400, statusText: "Bad Request"
      });
    }

    // Get the current status of the token
    let token = request.headers.get("Token");
    const value = await env.kv.get(token);

    // Check if the token is present in the database
    if(value === null) {
      return new Response(null, {
        status: 403, statusText: "Forbidden"
      });
    }

    if(action === "Bind") {

      // The token is not bound to a session, accept it
      if(value === "0") {
        
        // Bind the token
        try {
          await env.kv.put(token, "1");
        } catch(exception) {
          return new Response(null, {
            status: 500, statusText: "Internal Server Error"
          });
        }

        // Authentication worked, send the proper response
        return new Response(null, {
          status: 200, statusText: "OK"
        });
      }

      // The token is bound to a session, reject it
      else if(value === "1") {
        return new Response(null, {
          status: 403, statusText: "Forbidden"
        });
      }
    }
    else if(action === "Release") {

      // The token was bound to a session
      if(value === "1") {

        // Release the token
        try {
          await env.kv.put(token, "0");
        } catch(exception) {
          return new Response(null, {
            status: 500, statusText: "Internal Server Error"
          });
        }

        // Release worked, send the response
        return new Response(null, {
          status: 200, statusText: "OK"
        });
      }
    }

    // Generic catch-all error
    return new Response(null, {
      status: 500, statusText: "Internal Server Error"
    });
  },
};
