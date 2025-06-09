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

	const isHome = router.pathname === "/";
	const isProject =
		router.pathname.startsWith("/project") ||
		router.asPath.startsWith("/project");

	const handleProjectClick = () => {
		if (projectId) router.push(`/project/${projectId}`);
	};

	return (
		<nav>
			<div className="flex flex-wrap gap-1 mb-4" id="top-cards">
				<TopCard
					title="SYNTHPUB"
					subtitle="INFORMATION CULTURE"
					imageSrc={Logo}
					onClick={() => router.push("/")}
				/>

				{isHome && (
					<>
						<TopCard
							subtitle={"CREATE\nNEW PROJECT"}
							onClick={() => setIsModalOpen?.(true)}
						/>
						<TopCard
							subtitle={"SETTINGS"}
							onClick={() => setShowSettingsModal(true)}
						/>
					</>
				)}

				{isProject && (
					<>
						<TopCard subtitle={title} onClick={handleProjectClick} />
						<TopCard
							bgColor="bg-topCardBgSecond"
							textColor="text-topCardTextSecond"
							subtitle="CREATE NEW TOPIC"
							onClick={() => setIsModalOpen?.(true)}
						/>
						{["LATEST", "OLDEST", "MOST ACTIVE"].map((label) => (
							<TopCard
								key={label}
								bgColor="bg-topCardBgSecond"
								textColor="text-topCardTextSecond"
								subtitle={`${label} TOPIC`}
							/>
						))}
						<TopCard
							bgColor="bg-topCardBgLast"
							subtitle="MOST ACTIVE ARTICLE"
						/>
					</>
				)}

				{!isHome && !isProject && (
					<TopCard subtitle={title} onClick={handleProjectClick} />
				)}
			</div>

			{showSettingsModal && (
				<SettingsModal onClose={() => setShowSettingsModal(false)} />
			)}
		</nav>
	);
};

export default Navbar;
