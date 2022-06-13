import { CircleLoading } from '../../assets/icons';
export const Loading = () => { 
  const { type } = <CircleLoading />;

  return <img src={ type} />;
};