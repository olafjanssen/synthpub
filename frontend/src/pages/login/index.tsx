import type { NextPage } from "next";
import dynamic from "next/dynamic";

const Login = dynamic(
	() => import("@/features/login").then((mod) => mod.default),
	{
		loading: () => <div>Loading...</div>,
		ssr: false,
	}
);

const Home: NextPage = () => {
	return <Login />;
};

export default Home;
