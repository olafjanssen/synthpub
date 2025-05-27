const EmptyCard: React.FC = () => {
	return (
		<div className="w-56 shadow-[0.3em_0.3em_0px_#4a6a5f] flex flex-col bg-darkGreen text-white p-2">
			<div className="h-56 bg-lightGreen"></div>
			<div className="p-2 flex flex-col">
				<h5 className="text-base font-normal">&nbsp;</h5>
			</div>
			<div className="p-2 border-t border-transparent h-20">
				<p>&nbsp;</p>
			</div>
		</div>
	);
};

export default EmptyCard;
