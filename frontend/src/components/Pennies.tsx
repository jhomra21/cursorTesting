import React from 'react';
import { Link } from 'react-router-dom';

interface PennyBox {
  price: number;
  pennies: number;
}

const pennyBoxes: PennyBox[] = [
  { price: 10, pennies: 100 },
  { price: 25, pennies: 250 },
  { price: 50, pennies: 500 },
  { price: 100, pennies: 1000 },
];

const Pennies: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Buy Pennies</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {pennyBoxes.map((box) => (
          <div key={box.price} className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold mb-2">${box.price}</h2>
            <p className="text-gray-600 mb-4">{box.pennies} pennies</p>
            <Link
              to="/pennies"
              className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
            >
              Buy Now
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Pennies;