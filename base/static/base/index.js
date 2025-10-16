  const confirm1 = document.getElementById('confirmpassword');
  const password = document.getElementsByClassName('password')[0];
  const password2 = document.getElementsByClassName('password2')[0];
  const show = document.getElementsByClassName('showpassword')[0];
  const show1 = document.getElementsByClassName('showpassword1')[0];

  function togglePasswords() {
      const areHidden = 
          confirm1.type === 'password' &&
          password.type === 'password' &&
          password2.type === 'password';

      const newType = areHidden ? 'text' : 'password';

      confirm1.type = newType;
      password.type = newType;
      password2.type = newType;
  }

  show.addEventListener('click', togglePasswords);
  show1.addEventListener('click', togglePasswords);


  document.getElementsByClassName('login-header-div')[0].style.color = 'green';

