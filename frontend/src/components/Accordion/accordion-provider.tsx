// components/Accordion.tsx
import { ReactElement, isValidElement, Children } from "react";
import { AccordionDetailsProps } from "./accordion-details";

type AccordionProps = {
	children:
		| ReactElement<AccordionDetailsProps>
		| ReactElement<AccordionDetailsProps>[];
};

const Accordion: React.FC<AccordionProps> = ({ children }) => {
	Children.forEach(children, (child) => {
		if (!isValidElement(child)) {
			throw new Error("Accordion only accepts AccordionDetails components.");
		}
	});

	return (
		<div className="w-full divide-y divide-gray-200 border border-gray-300 rounded-xl bg-white shadow-sm">
			{children}
		</div>
	);
};

export default Accordion;
