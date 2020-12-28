/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'mapfdev.us', // the auth0 domain prefix
    audience: 'coffeeapp', // the audience set for the auth0 app
    clientId: 'CDWsr2U0UV7IjKzLdjKihi9OPqIy4XR5', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
