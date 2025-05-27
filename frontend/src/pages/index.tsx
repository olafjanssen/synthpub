import type { NextPage } from "next";
import Dashboard from "@/features/dashboard";
import Navbar from "@/components/Navbar";
import { useState } from "react";

const Home: NextPage = () => {
	const [isModalOpen, setIsModalOpen] = useState(false);
	return (
		<div>
			<Navbar setIsModalOpen={setIsModalOpen} />
			<Dashboard isModalOpen={isModalOpen} setIsModalOpen={setIsModalOpen} />
		</div>
	);
};

export default Home;
