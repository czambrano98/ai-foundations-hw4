import { Link } from 'react-router-dom'

export default function About() {
  return (
    <div className="page">
      <div className="shell prose">
        <div className="eyebrow">57 Broadway, New Haven</div>
        <h1>About Us</h1>

        <p>
          Campus Customs opened on Broadway in 1973, and we have been making Yale
          clothing in New Haven ever since. It started as a small shop selling
          memorabilia. It is still a family business, now with a print room, a row
          of embroidery machines, and fifty years of knowing exactly how a crest
          should sit on a chest.
        </p>

        <p className="pull">
          We are not a catalogue that drop-ships from a warehouse you will never
          see. We are a few people in New Haven who make the thing, then hand it
          to you.
        </p>

        <h2>How we make it</h2>
        <p>
          Nearly everything we sell is printed or embroidered in house. That is a
          slower way to run a clothing company, and it is the only way we know how
          to keep the quality honest. We pick heavyweight cotton because it holds
          its shape. We use ribbed cuffs and hems because they survive being
          pushed up a hundred times in a library. When a color comes out half a
          shade off, it does not ship. It goes back on the press.
        </p>
        <p>
          The practical version: you should be able to wear one of our crewnecks
          through four winters, graduate in it, and still reach for it a decade
          later. That is the whole standard.
        </p>

        <h2>Who we make it for</h2>
        <p>
          Yale is not one thing. It is fourteen residential colleges that each
          think they are the best one. It is the School of Management and the
          Divinity School and the School of Art. It is twenty-some varsity teams,
          the Game every November, and a cappella groups with strong opinions
          about blazers.
        </p>
        <p>
          So we make gear for all of it, including for the people who never set
          foot in a seminar here. The parents, the grandparents, the uncle who
          mentions your school to his dentist. Belonging to this place was never
          only about the person holding the degree, and our shelves reflect that.
        </p>

        <h2>Come find us</h2>
        <p>
          We are at 57 Broadway, a short walk from Old Campus. Come in and feel
          the weight of the cotton before you buy it. That is genuinely the best
          way to shop for a sweatshirt. If you cannot make it in, the shop
          assistant in the corner of this page can help you find your size.
        </p>

        <Link to="/products" className="btn btn-primary">
          Browse the collection
        </Link>
      </div>
    </div>
  )
}
