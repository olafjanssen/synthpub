import type { NextPage } from "next";
import Navbar from "@/features/nav-bar/Navbar";
import { useState } from "react";
import dynamic from "next/dynamic";

const Home: NextPage = () => {
	const [isModalOpen, setIsModalOpen] = useState(false);

	const Dashboard = dynamic(
		() => import("@/features/dashboard").then((mod) => mod.default),
		{
			loading: () => <div>Loading...</div>,
			ssr: true,
		}
	);
	return (
		<>
			<Navbar setIsModalOpen={setIsModalOpen} />
			<Dashboard isModalOpen={isModalOpen} setIsModalOpen={setIsModalOpen} />
		</>
	);
};

export default Home;
