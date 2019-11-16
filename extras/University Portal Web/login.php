<html>

<head>
	<title>Login Page</title>
	<style type="text/css">
		body {
			font-family: Arial, Helvetica, sans-serif;
			font-size: 14px
		}
		
		label {
			font-weight: bold;
			width: 100px;
			font-size: 14px;
		}
		
		.box {
			border: #666666 solid 1px;
		}
		
		.container{
			width: 30%;
			border: solid 2px #333;
			border-radius: 10%;
		}
		
		input {
			margin: .4em;
		}
	</style>

</head>

<body>
	<div align="center">
		<div class="container">
			<div style="background-color:#abccab; color:#FFFFFF;padding: 1em;">
				<b>Login</b>
			</div>
			<div style="padding: 20px">
				<form action="login.php" method="post">
					<label>Username  :</label>
					<input type="text" name="username" class="box"/>
					<br>
					<label>Password  :</label>
					<input type="password" name="password" class="box"/>
					<br>
					<input type="radio" name="userType" value="Admin" id="individual"/>
					<label>Individual</label>
					<input type="radio" name="userType" value="Instructor" id="individual"/>
					<label>Organization</label>
					<input type="radio" name="userType" value="Student" id="student"/>
					<label>Student</label>
					<br>
					<input type="submit" value=" Login "/>
				</form>
			</div>
		</div>
	</div>
</body>

</html>
<?php 
if($_POST){	
if($_POST['username']=="admin" && $_POST['password']=="admin"){		
header("location:welcome.php");	
}else{		
echo "failed";		
}
}
?>