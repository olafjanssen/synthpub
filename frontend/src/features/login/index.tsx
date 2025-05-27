import React, { useState } from "react";
import Button from "@/components/Button";
import { useRouter } from "next/router";
//import Link from "next/link";

const Login: React.FC = () => {
	const router = useRouter();
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	//const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		// setLoading(true);
		setError(null);
		router.push("/");
	};

	return (
		<div className="flex items-center justify-center min-h-screen">
			<div className="max-w-md w-full p-6 bg-[#4A6A5F] text-white shadow-md rounded-md">
				<h2 className="text-2xl font-bold mb-4">Login</h2>
				<form onSubmit={handleSubmit}>
					<div className="mb-4">
						<label htmlFor="email" className="block text-white mb-2">
							Email
						</label>
						<input
							type="email"
							id="email"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							className="w-full p-2 border border-gray-300 rounded"
							required
						/>
					</div>
					<div className="mb-4">
						<label htmlFor="password" className="block text-white mb-2">
							Password
						</label>
						<input
							type="password"
							id="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							className="w-full p-2 border border-gray-300 rounded"
							required
						/>
					</div>
					{error && <p className="text-red-500 mb-4">{error}</p>}
					<Button title="Login" className="w-full" />
				</form>
				{/* <p className="mt-4 text-center">
      Don&apos;t have an account? <Link href="/signup">Sign Up</Link>
    </p> */}
			</div>
		</div>
	);
};

export default Login;
