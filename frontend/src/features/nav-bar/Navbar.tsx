import { useState } from "react";
import { useRouter } from "next/router";
import Logo from "@/assets/images/dpbtse_logo.png";
import SettingsModal from "../settings";
import TopCard from "../../components/cards/TopCard";

interface Props {
	setIsModalOpen?: (ele: boolean) => void;
	title?: string;
	projectId?: string;
}

const Navbar: React.FC<Props> = ({ setIsModalOpen, title, projectId }) => {
	const router = useRouter();
	const [showSettingsModal, setShowSettingsModal] = useState(false);

	return (
		<nav>
			<div className="flex flex-wrap gap-1 mb-4" id="top-cards">
				<TopCard
					title="SYNTHPUB"
					subtitle="INFORMATION CULTURE"
					imageSrc={Logo}
					onClick={() => router.push("/")}
				/>
				{router.pathname === "/" ? (
					<>
						<TopCard
							subtitle={"CREATE\nNEW PROJECT"}
							onClick={() => setIsModalOpen && setIsModalOpen(true)}
						/>
						<TopCard
							subtitle={"SETTINGS"}
							onClick={() => setShowSettingsModal(true)}
						/>
					</>
				) : (
					<>
						<TopCard
							subtitle={title}
							onClick={() => {
								router.push(`/project/${projectId}`);
							}}
						/>

						<TopCard
							bgColor="bg-topCardBgSecond"
							textColor="text-topCardTextSecond"
							subtitle={"CREATE NEW TOPIC"}
							onClick={() => setIsModalOpen && setIsModalOpen(true)}
						/>
						<TopCard
							bgColor="bg-topCardBgSecond"
							textColor="text-topCardTextSecond"
							subtitle={"LATEST TOPIC"}
						/>
						<TopCard
							bgColor="bg-topCardBgSecond"
							textColor="text-topCardTextSecond"
							subtitle={"OLDEST TOPIC"}
						/>
						<TopCard
							bgColor="bg-topCardBgSecond"
							textColor="text-topCardTextSecond"
							subtitle={"MOST ACTIVE TOPIC"}
						/>
						<TopCard
							bgColor="bg-topCardBgLast"
							subtitle={"MOST ACTIVE ARTICLE"}
						/>
					</>
				)}
			</div>
			{showSettingsModal && (
				<SettingsModal onClose={() => setShowSettingsModal(false)} />
			)}
		</nav>
	);
};

export default Navbar;
